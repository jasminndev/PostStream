import mimetypes
import uuid

from django.core.files.storage import Storage
from supabase import create_client

from core.config import SupabaseConfig


class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(SupabaseConfig.SUPABASE_URL, SupabaseConfig.SUPABASE_KEY)
        self.bucket_name = SupabaseConfig.SUPABASE_BUCKET

    def deconstruct(self):
        return (
            'core.storage.SupabaseStorage',
            [],
            {}
        )

    def _save(self, name, content):

        ext = name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'

        file_content = content.read()

        self.client.storage.from_(self.bucket_name).upload(
            filename,
            file_content,
            file_options={"content-type": content_type}
        )

        return filename

    def _open(self, name, mode='rb'):
        raise NotImplementedError("Opening files from Supabase is not supported")

    def exists(self, name):
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            return any(f['name'] == name for f in files)
        except:
            return False

    def url(self, name):
        if not name:
            return None
        return self.client.storage.from_(self.bucket_name).get_public_url(name)

    def delete(self, name):
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except:
            pass

    def size(self, name):
        return 0
