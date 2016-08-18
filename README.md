# lofirrtl2ilang

This is a small python package that converts Chisel LoFIRRTL into Yosys ilang.

## Status

It kinda sorta works for some LoFIRRTL.

## What is LoFIRRTL?
* Scala is a functional language that targets the JVM. It's kinda like Java but more functional. It's somewhat popular in academic circles.
* Chisel is a Scala-based HDL associated with Berkeley and the RISC-V ISA.
* FIRRTL is an intermediate represtation language (and a compiler?) used by the more recent implementations of Chisel.
* LoFIRRTL is a subset of FIRRTL that is almost down to netlist level complexity.

## What is ilang?
* Yosys is a open-source hardware synthesis tool. It's super neat
* ilang is the intermediate representation language used by Yosys

## Why is this useful?
Honestly, it's not that useful. Right now, the firrtl compiler tends to compile down to Verilog. Verilog can be parsed by almost everything, including Yosys.

But in an ideal world, our HDL's could stop transpiling into Verilog and we could go straight down to a netlist level format and stay there. So this project is an attempt at bridging Chisel and Yosys without resorting to generating Verilog.
