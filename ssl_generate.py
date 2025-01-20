from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.hashes import SHA256
from datetime import datetime, timedelta, timezone

# Generowanie klucza prywatnego
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Dane certyfikatu
now = datetime.now(timezone.utc)
valid_from = now
valid_until = now + timedelta(days=365)

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"PL"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Organization"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    valid_from
).not_valid_after(
    valid_until
).sign(private_key, SHA256())

# Zapisywanie klucza prywatnego
with open("key.pem", "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

# Zapisywanie certyfikatu
with open("cert.pem", "wb") as f:
    f.write(
        cert.public_bytes(serialization.Encoding.PEM)
    )

print("Certyfikat i klucz wygenerowane!")
