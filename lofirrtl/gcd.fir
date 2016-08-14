circuit GCD :
  module GCD :
    input e : UInt<1>
    input clk : Clock
    input reset : UInt<1>
    output z : UInt
    output v : UInt<1>
    input a : UInt<16>
    input b : UInt<16>
    reg x : UInt<16>,clk
    reg y : UInt<16>,clk
    node T_17 = gt(x, y)
    when T_17 :
        node T_18 = tail(sub(x, y), 1)
        x <= T_18
    else :
        node T_19 = tail(sub(y, x), 1)
        y <= T_19
    when e :
        x <= a
        y <= b
    z <= x
    node T_20 = eq(y, UInt<1>(0))
    v <= T_20