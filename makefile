default: all

all:
    cd maptoolslib
    cargo build
    cd ..
    
    
    copy maptoolslib\target\debug\maptoolslib.dll app\src\maptoolslib.pyd
    
run: all
    app\main.py
    
clean:
    cd maptoolslib
    cargo clean
    cd ..
    
    del app\src\maptoolslib.pyd
    