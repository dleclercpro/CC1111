CC = sdcc

CODEFLAGS = \
	--model-small \
	--opt-code-speed \
	--stack-auto

CFLAGS = $(CODEFLAGS)

LDFLAGS = \
	--out-fmt-ihx \
	--code-loc 0x0000 \
	--xram-loc 0xF000 \
	--code-size 0x8000 \
	--xram-size 0x0F00 \
	--iram-size 0x0100

ifdef DEBUG
CFLAGS += --debug
endif

PROGS = main.hex
SRC = main.c lib.c clock.c timer.c led.c usb.c command.c interrupts.c
ADB = $(SRC:.c=.adb)
ASM = $(SRC:.c=.asm)
LNK = $(SRC:.c=.lnk)
LST = $(SRC:.c=.lst)
REL = $(SRC:.c=.rel)
RST = $(SRC:.c=.rst)
SYM = $(SRC:.c=.sym)
PCDB = $(PROGS:.hex=.cdb)
PLNK = $(PROGS:.hex=.lnk)
PMAP = $(PROGS:.hex=.map)
PMEM = $(PROGS:.hex=.mem)
PAOM = $(PROGS:.hex=)

%.rel : %.c
	$(CC) -c $(CFLAGS) -o $*.rel $<

all: $(PROGS) clean

main.hex: $(REL) Makefile
	$(CC) $(LDFLAGS) $(CFLAGS) -o main.hex $(REL)

install:
	sudo cc-tool -v -e -w main.hex

clean:
	rm -f $(ADB) $(ASM) $(LNK) $(LST) $(REL) $(RST) $(SYM)
	rm -f $(PCDB) $(PLNK) $(PMAP) $(PMEM) $(PAOM)
	#rm -f $(PROGS)