import sys
import uvicorn


def main():
    if "--gui" in sys.argv:
        from gui.interface import FirewallGUI
        app = FirewallGUI()
        app.run()
    else:
        print("Starting NetFort Web Firewall Simulator at http://127.0.0.1:8000 ...")
        uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()