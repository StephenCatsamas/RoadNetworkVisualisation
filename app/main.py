from src import ui,maptoolslib

def run():
    print('Initiating road network visualisation')
    print(maptoolslib.__doc__)
    print(maptoolslib.rust_test(43))
    ui.begin()

if __name__ == "__main__":
    run()
    

