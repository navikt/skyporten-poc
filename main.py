import json
import jwt
import os
import uuid
import requests
from datetime import datetime, timezone, timedelta
from jwt.algorithms import RSAAlgorithm
from google.cloud import storage
from google.auth import identity_pool

issuer = "https://test.sky.maskinporten.no"

jwk = os.getenv('MASKINPORTEN_CLIENT_JWK')
client_id = os.getenv('MASKINPORTEN_CLIENT_ID')

header = {
    "kid": json.loads(jwk)['kid']
}

payload = {
    "aud": issuer,
    "iss": client_id,
    "scope": "entur:skyporten.demo",
    "resource": 'https://skyporten.entur.org',
    "iat": datetime.now(tz=timezone.utc),
    "exp": datetime.now(tz=timezone.utc)+timedelta(minutes=1),
    "jti": str(uuid.uuid4())
}

private_key = RSAAlgorithm.from_jwk(jwk)
grant = jwt.encode(payload, private_key, "RS256", header)

body = {
    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    'assertion': grant
}

res = requests.post(issuer+"/token", data=body)
if res.status_code != 200:
    raise Exception(res.text)

payload = json.loads(res.text)

with open('/tmp/access_token', 'w', encoding="utf-8") as f:
    f.write(payload['access_token'])

google_project_num = "207740593944"

json_config_info = {
    "type": "external_account",
    "audience": f"//iam.googleapis.com/projects/{google_project_num}/locations/global/workloadIdentityPools/skyporten-public-demo/providers/skyporten-test",
    "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
    "token_url": "https://sts.googleapis.com/v1/token",
    "credential_source": {
        "file": "/tmp/access_token"
    },
    "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/skyporten-public-demo-consumer@ent-data-sdsharing-ext-dev.iam.gserviceaccount.com:generateAccessToken",
}

credentials = identity_pool.Credentials.from_info(json_config_info)

project_id = 'ent-data-sdsharing-ext-dev'
storage_client = storage.Client(project=project_id, credentials=credentials)
source_bucket = storage_client.bucket("skyporten-public-demo")
destination_bucket = storage_client.bucket("skyporten-poc-ssb")

for blob in list(storage_client.list_blobs("skyporten-public-demo")):
    source_blob = source_bucket.blob(blob.name)
    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, blob.name
    )

    print(
        "Blob {} in bucket {} copied to blob {} in bucket {}.".format(
            source_blob.name,
            source_bucket.name,
            blob_copy.name,
            destination_bucket.name,
        ))
