# To Generate Compile Files:


pip-compile --generate-hashes --output-file base.txt base.in
pip-compile --generate-hashes --output-file dev.txt dev.in
pip-compile --generate-hashes --output-file staging.txt staging.in
pip-compile --generate-hashes --output-file production.txt production.in


Recompile whenever you change .in files:
pip-compile --upgrade --generate-hashes -o base.txt base.in
<!-- repeat for others if needed -->



## Install per environment
1. Dev/local


    pip install -r requirements/dev.txt


2. Staging


    pip install --require-hashes -r requirements/staging.txt

3. Production


    pip install --require-hashes -r requirements/production.txt


- Use --require-hashes in CI/CD to ensure exact, verified wheels are installed.



Command : 
python3 manage.py seed_roles



Curl Commands:

- register a user:

curl -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Request-ID: $REQ_ID" \
  --data-raw '{
    "username": "ali",
    "email": "ali@example.com",
    "password": "VeryStrong!Pass1"
  }'



# JWT Keys

# 4096-bit RSA private key
openssl genrsa -out jwtRS256.key 4096

# Public key derived from the private key
openssl rsa -in jwtRS256.key -pubout -out jwtRS256.key.pub


Update .env files

JWT_PRIVATE_KEY_FILE=jwtRS256.key
JWT_PUBLIC_KEY_FILE=jwtRS256.key.pub