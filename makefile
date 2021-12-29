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
    app\main.py

runr: rust
    @del outfile.png
    @maptoolslib\target\debug\maptools.exe
    @outfile.png

clean:
    cd maptoolslib
    cargo clean
    cd ..
    
    del app\src\maptoolslib.pyd
    