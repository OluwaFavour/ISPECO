# Deploying your application to the cloud

First, add a .env file to the root of your project with the following content:

- SECRET_KEY
- DATABASE_URL
- EMAIL_HOST_PASSWORD
- FERNET_KEY
- SUPERUSER_PASSWORD
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- PAYPAL_CLIENT_ID
- PAYPAL_SECRET
- ISPECO_SERVER_URL
- EMAIL_HOST
- EMAIL_HOST_USER
- EMAIL_PORT
- EMAIL_USE_TLS
- DEFAULT_FROM_EMAIL
- SERVER_EMAIL

Build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

## Next steps

Run the image on your cloud provider, e.g.: `docker run --env_file .env myregistry.com/myapp`.

### References

- [Docker's Python guide](https://docs.docker.com/language/python/)
