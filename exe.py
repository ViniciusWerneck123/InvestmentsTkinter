from app import *

if __name__=='__main__':
    app = App()
    app.root.protocol('WM_DELETE_WINDOW', app.on_closing)
    app.root.mainloop()