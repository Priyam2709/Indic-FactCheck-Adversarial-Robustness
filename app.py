from framework.ui.app import demo

if __name__ == "__main__":
    # Hugging Face Spaces handles the port and server binding automatically.
    # This root-level script allows native integration with HF Spaces and other cloud PaaS.
    demo.launch()
