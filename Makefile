TARGETS=all check clean clobber distclean install uninstall
TARGET=all

PREFIX=${DESTDIR}/opt
BINDIR=${PREFIX}/bin
SUBDIRS=

ifeq	(${MAKE},gmake)
	INSTALL=ginstall
else
	INSTALL=install
endif

.PHONY: ${TARGETS} ${SUBDIRS}

all::	asl.py

${TARGETS}::

clobber distclean:: clean

ARGS	=samples/AdminServer.log

check::	asl.py
	python ./asl.py ${ARGS}

install:: asl.py
	${INSTALL} -D asl.py ${BINDIR}/asl

uninstall::
	${RM} ${BINDIR}/asl

ifneq	(,${SUBDIRS})
${TARGETS}::
	${MAKE} TARGET=$@ ${SUBDIRS}
${SUBDIRS}::
	${MAKE} -C $@ ${TARGET}
endif
