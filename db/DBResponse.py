class DBResponse:
    def __init__(self, success, record_id=None, record=None, error=None):
        self.success = success
        self.record_id = record_id
        self.error = error
        self.record = record

    def __repr__(self):
        return f"DBResponse(success={self.success}, record_id={self.record_id}, error={self.error})"
