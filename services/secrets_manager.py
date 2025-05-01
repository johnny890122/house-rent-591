import json, os, sys
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(parent_dir)
class SecretsManager:
    """
    Singleton for AWS Secrets Manager that supports an explicit profile.
    """
    _instance = None 

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        load_dotenv(dotenv_path=".env", override=True)
        secret_name = os.environ.get("SECRET_NAME")
        region_name = os.environ.get("AWS_REGION")
        profile_name = os.environ.get("AWS_PROFILE")

        inst = super().__new__(cls)
        inst._secret_name  = secret_name
        inst._region_name  = region_name
        inst._profile_name = profile_name

        # Create a session with optional profile
        session = boto3.Session(
            profile_name=inst._profile_name, region_name=inst._region_name
        )
        inst._client = session.client("secretsmanager")
        inst._cache  = None
        cls._instance = inst
        
        return cls._instance

    def _fetch_secret(self) -> dict:
        try:
            resp = self._client.get_secret_value(SecretId=self._secret_name)
        except ClientError as e:
            raise RuntimeError(f"Unable to fetch secret {self._secret_name}") from e

        secret_str = resp.get("SecretString") or resp["SecretBinary"].decode("utf-8")
        return json.loads(secret_str)

    def get_secrets(self) -> dict:
        if self._cache is None:
            self._cache = self._fetch_secret()
        return self._cache

    def get(self, key: str) -> str:
        try:
            return self.get_secrets()[key]
        except KeyError:
            raise KeyError(f"Key {key} not found in secrets")

    @property
    def mongo_uri(self) -> str:
        return self.get("MONGO_URI")

    @property
    def line_token(self) -> str:
        return self.get("LINE_TOKEN")

    @property
    def db_connection(self) -> dict:
        return self.get("DB_CONNECTIONS")