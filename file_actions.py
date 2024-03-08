
def upload_file(smb_conn, input_file, upload_location):    
    with open(input_file, "rb") as file:
        try:
            print(f"{input_file=}, {upload_location=}")
            smb_conn.putFile("C$", upload_location, file.read)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False