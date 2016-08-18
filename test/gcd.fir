circuit GCD :
  module GCD :
    input e : UInt<1>
    input clk : Clock
    input reset : UInt<1>
    output z : UInt<16>
    output v : UInt<1>
    input a : UInt<16>
    input b : UInt<16>
  
    reg x : UInt<16>, clk with :
      reset => (UInt<1>("h0"), x)
    reg y : UInt<16>, clk with :
      reset => (UInt<1>("h0"), y)
    node T_17 = gt(x, y)
    node T_18 = tail(sub(x, y), 1)
    node T_19 = tail(sub(y, x), 1)
    node GEN_0 = mux(T_17, T_18, x)
    node GEN_1 = mux(T_17, y, T_19)
    node GEN_2 = mux(e, a, GEN_0)
    node GEN_3 = mux(e, b, GEN_1)
    node T_20 = eq(y, UInt<1>("h0"))
    z <= x
    v <= T_20
    x <= GEN_2
    y <= GEN_3
