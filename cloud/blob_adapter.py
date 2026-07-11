"""
blob_adapter.py
=================
Real Azure SDK integration point for Azure Blob Storage (the brief's storage
requirement, #8 on the approved services list — Hot tier for actively-accessed
demo data) — storing produce listing photos/documents. This is the one piece
of the architecture wired to genuinely call Azure, not simulated, so the
deployment has at least one live managed-service integration alongside the
locally-run engines.

Usage requires an Azure Storage connection string (from the Storage Account's
"Access keys" blade, or a Managed Identity when running on an Azure VM/Function,
per the program's guidance to avoid embedding credentials in code).

Install: pip install azure-storage-blob azure-identity
"""

from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceNotFoundError, AzureError


class BlobProduceStore:
    def __init__(self, connection_string: str = None, account_url: str = None,
                 credential=None, container_name: str = "produce-images"):
        """
        Two auth paths, matching program guidance:
          - connection_string: simplest for local/dev use
          - account_url + credential (e.g. azure.identity.ManagedIdentityCredential
            or DefaultAzureCredential): for production, avoids embedding keys in code
        """
        if connection_string:
            self.client = BlobServiceClient.from_connection_string(connection_string)
        elif account_url and credential:
            self.client = BlobServiceClient(account_url=account_url, credential=credential)
        else:
            raise ValueError("Provide either connection_string, or account_url + credential")

        self.container_name = container_name
        self.container_client = self.client.get_container_client(container_name)
        if not self.container_client.exists():
            self.container_client = self.client.create_container(container_name)

    def upload_listing_image(self, local_path: str, listing_id: str) -> str:
        blob_name = f"listings/{listing_id}/{local_path.split('/')[-1]}"
        blob_client = self.container_client.get_blob_client(blob_name)
        try:
            with open(local_path, "rb") as f:
                blob_client.upload_blob(
                    f, overwrite=True,
                    content_settings=ContentSettings(content_type="image/jpeg"),
                )
            return blob_client.url
        except AzureError as e:
            raise RuntimeError(f"Blob upload failed: {e}")

    def list_listing_images(self, listing_id: str) -> list:
        prefix = f"listings/{listing_id}/"
        try:
            return [b.name for b in self.container_client.list_blobs(name_starts_with=prefix)]
        except AzureError as e:
            raise RuntimeError(f"Blob list failed: {e}")

    def delete_listing_images(self, listing_id: str):
        for name in self.list_listing_images(listing_id):
            try:
                self.container_client.delete_blob(name)
            except ResourceNotFoundError:
                pass


if __name__ == "__main__":
    print("BlobProduceStore requires a real Azure Storage Account + container to run live.")
    print("Example usage:")
    print("  store = BlobProduceStore(connection_string='<from Storage Account Access Keys>')")
    print("  store.upload_listing_image('tomato.jpg', 'LST-000123')")
