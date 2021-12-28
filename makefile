default: all

rust:
    @cd maptoolslib
    cargo build --release
    @cd ..

all: rust    
    copy maptoolslib\target\release\maptoolslib.dll app\src\maptoolslib.pyd
    
run: all
    app\main.py

runr: rust
    @del outfile.png
    @maptoolslib\target\release\maptools.exe
    @outfile.png

clean:
    cd maptoolslib
    cargo clean
    cd ..
    
    del app\src\maptoolslib.pyd
    