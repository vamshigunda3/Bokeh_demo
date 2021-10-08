from . import d_files
def on_server_loaded(server_context):
    d_files.update_data()
    print("you came to hooks")
