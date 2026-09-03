import datetime
from unittest import TestCase

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from OpenSSL import crypto

from seleniumwire.thirdparty.mitmproxy.certs import Cert


class CertTest(TestCase):
    def test_altnames_with_modern_pyopenssl(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.com")])
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=1)
            )
            .add_extension(
                x509.SubjectAlternativeName(
                    [x509.DNSName("example.com"), x509.DNSName("www.example.com")]
                ),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )
        pyopenssl_cert = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            certificate.public_bytes(serialization.Encoding.PEM),
        )

        self.assertFalse(hasattr(pyopenssl_cert, "get_extension"))
        self.assertEqual(
            [b"example.com", b"www.example.com"], Cert(pyopenssl_cert).altnames
        )
