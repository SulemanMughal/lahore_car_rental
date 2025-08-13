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
