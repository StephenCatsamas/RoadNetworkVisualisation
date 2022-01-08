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

all: rust    
    copy  $(LIBFP)\maptoolslib.dll $(PYDFP)\maptoolslib.pyd
 
run: all
    @cd app
    main.py
    @cd ..

runr: rust-bin
    copy $(LIBFP)\maptools.exe dbg\maptools.exe
    @cd dbg
    @maptools.exe
    @cd ..

.PHONY: clean
clean:
    cd $(LIBDIR) 
    cargo clean
    cd ..
    
    del $(PYDFP)\maptoolslib.pyd
    