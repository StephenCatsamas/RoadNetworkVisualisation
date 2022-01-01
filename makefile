default: all

rust:
    @cd maptoolslib
    cargo build
    @cd ..

rustt:
    @cd maptoolslib
    cargo test 
    @cd ..

all: rust    
    copy maptoolslib\target\debug\maptoolslib.dll app\src\maptoolslib.pyd
    
run: all
    @cd app
    main.py
    @cd ..
    
runr: rust
    @maptoolslib\target\debug\maptools.exe

clean:
    cd maptoolslib
    cargo clean
    cd ..
    
    del app\src\maptoolslib.pyd
    