import requests
import time
from typing import List, Dict, Optional

class VectorStoreClient:
    def __init__(self, api_key: str):
        self.base_url = "https://api.openai.com/v1/vector_stores"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }

    # Vector Store Operations
    def create_vector_store(
        self,
        name: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        expires_after: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Erstellt einen neuen Vector Store"""
        data = {}
        if name: data["name"] = name
        if file_ids: data["file_ids"] = file_ids
        if expires_after: data["expires_after"] = expires_after
        if metadata: data["metadata"] = metadata
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=data
        )
        return self._handle_response(response)

    def get_vector_store(self, vector_store_id: str) -> Dict:
        """Holt einen spezifischen Vector Store"""
        response = requests.get(
            f"{self.base_url}/{vector_store_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def update_vector_store(
        self,
        vector_store_id: str,
        name: Optional[str] = None,
        expires_after: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Aktualisiert einen Vector Store"""
        data = {}
        if name: data["name"] = name
        if expires_after: data["expires_after"] = expires_after
        
        response = requests.post(
            f"{self.base_url}/{vector_store_id}",
            headers=self.headers,
            json=data
        )
        return self._handle_response(response)

    def delete_vector_store(self, vector_store_id: str) -> Dict:
        """Löscht einen Vector Store"""
        response = requests.delete(
            f"{self.base_url}/{vector_store_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def list_vector_stores(self) -> List[Dict]:
        """Listet alle Vector Stores auf"""
        response = requests.get(
            self.base_url,
            headers=self.headers
        )
        return self._handle_response(response).get("data", [])

    # File Operations
    def upload_file(
        self,
        vector_store_id: str,
        file_path: str,
        chunk_size: int = 512
    ) -> Dict:
        """Lädt eine Datei in einen Vector Store hoch"""
        upload_url = f"{self.base_url}/{vector_store_id}/files"
        
        with open(file_path, "rb") as file:
            response = requests.post(
                upload_url,
                headers={
                    **self.headers,
                    "Content-Type": "application/octet-stream"
                },
                data=file.read()
            )
        return self._handle_response(response)

    def list_files(
        self,
        vector_store_id: str,
        filter: Optional[str] = None
    ) -> List[Dict]:
        """Listet Dateien in einem Vector Store auf"""
        url = f"{self.base_url}/{vector_store_id}/files"
        params = {"filter": filter} if filter else None
        
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        return self._handle_response(response).get("data", [])

    def delete_file(
        self,
        vector_store_id: str,
        file_id: str
    ) -> Dict:
        """Löscht eine Datei aus einem Vector Store"""
        response = requests.delete(
            f"{self.base_url}/{vector_store_id}/files/{file_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    # Helper Methods
    def _handle_response(self, response: requests.Response) -> Dict:
        """Behandelt API-Antworten"""
        if 200 <= response.status_code < 300:
            return response.json()
        raise Exception(f"API Fehler {response.status_code}: {response.text}")

    def poll_until_ready(
        self,
        vector_store_id: str,
        timeout: int = 300,
        interval: int = 5
    ) -> Dict:
        """Pollt den Vector Store bis er bereit ist"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_vector_store(vector_store_id)
            if status.get("status") == "completed":
                return status
            time.sleep(interval)
        raise TimeoutError("Vector Store wurde nicht rechtzeitig bereit")

# Beispielnutzung
if __name__ == "__main__":
    import os
    
    # Initialisierung
    client = VectorStoreClient(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Vector Store erstellen
    vs = client.create_vector_store(name="Mein erster Store")
    vs_id = vs["id"]
    
    # Datei hochladen
    file = client.upload_file(vs_id, "daten.pdf")
    
    # Auf Fertigstellung warten
    client.poll_until_ready(vs_id)
    
    # Store löschen
    client.delete_vector_store(vs_id)
