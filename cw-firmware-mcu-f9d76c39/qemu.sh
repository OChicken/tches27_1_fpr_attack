#!/bin/bash

QEMU=qemu-system-arm
QEMUFLAGS="-M mps2-an386 -nographic -semihosting"

$QEMU $QEMUFLAGS -kernel $1
