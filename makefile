default: all

!IF "$(G)" == "release"
CFLAGS = --release
RELEASE = release
!ELSE
RELEASE = debug
!ENDIF

CARGO = cargo
LIBDIR = maptoolslib
PYDFP = app\src
LIBFP = $(LIBDIR)\target\$(RELEASE)

rust:
    @cd $(LIBDIR) 
    $(CARGO) build $(CFLAGS)
    @cd ..

rust-bin:
    @cd $(LIBDIR) 
    $(CARGO) build $(CFLAGS) --bin maptools
    @cd ..

rust-test:
    @cd $(LIBDIR) 
    $(CARGO) test $(CFLAGS)
    @cd ..

all: rust    
    copy  $(LIBFP)\maptoolslib.dll $(PYDFP)\maptoolslib.pyd
 
run: all
    @cd app
    main.py
    @cd ..

rust-debug: rust-bin
    copy $(LIBFP)\maptools.exe dbg\maptools.exe

runr: rust-debug
    @cd dbg
    @maptools.exe
    @cd ..

test: rust-test
    


.PHONY: clean
clean:
    cd $(LIBDIR) 
    cargo clean
    cd ..
    
    del $(PYDFP)\maptoolslib.pyd
    