import os
from framework.ui.app import demo

if __name__ == "__main__":
    # Render.com injects the port dynamically via the PORT env variable
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
