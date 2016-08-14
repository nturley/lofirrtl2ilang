module \up3down5
  wire $0\borrow_out[0:0]
  wire $0\carry_out[0:0]
  wire width 10 $0\cnt_dn[9:0]
  wire width 10 $0\cnt_up[9:0]
  wire width 9 $0\count_nxt[8:0]
  wire width 9 $0\count_out[8:0]
  wire $0\parity_out[0:0]
  wire width 9 $1\count_nxt[8:0]
  wire width 10 $add$tests/simple/fiedler-cooley.v:17$3_Y
  wire $and$tests/simple/fiedler-cooley.v:28$5_Y
  wire $and$tests/simple/fiedler-cooley.v:29$6_Y
  wire $reduce_xor$tests/simple/fiedler-cooley.v:27$4_Y
  wire width 10 $sub$tests/simple/fiedler-cooley.v:16$2_Y
  wire output 6 \borrow_out
  wire output 5 \carry_out
  wire input 1 \clock
  wire width 10 \cnt_dn
  wire width 10 \cnt_up
  wire width 9 \count_nxt
  wire width 9 output 7 \count_out
  wire width 9 input 2 \data_in
  wire input 4 \down
  wire output 8 \parity_out
  wire input 3 \up
  cell $add $add$tests/simple/fiedler-cooley.v:17$3
    parameter \A_SIGNED 0
    parameter \A_WIDTH 9
    parameter \B_SIGNED 0
    parameter \B_WIDTH 2
    parameter \Y_WIDTH 10
    connect \A \count_out
    connect \B 2'11
    connect \Y $add$tests/simple/fiedler-cooley.v:17$3_Y
  end
  cell $and $and$tests/simple/fiedler-cooley.v:28$5
    parameter \A_SIGNED 0
    parameter \A_WIDTH 1
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 1
    connect \A \up
    connect \B $add$tests/simple/fiedler-cooley.v:17$3_Y [9]
    connect \Y $and$tests/simple/fiedler-cooley.v:28$5_Y
  end
  cell $and $and$tests/simple/fiedler-cooley.v:29$6
    parameter \A_SIGNED 0
    parameter \A_WIDTH 1
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 1
    connect \A \down
    connect \B $sub$tests/simple/fiedler-cooley.v:16$2_Y [9]
    connect \Y $and$tests/simple/fiedler-cooley.v:29$6_Y
  end
  cell $reduce_xor $reduce_xor$tests/simple/fiedler-cooley.v:27$4
    parameter \A_SIGNED 0
    parameter \A_WIDTH 9
    parameter \Y_WIDTH 1
    connect \A $1\count_nxt[8:0]
    connect \Y $reduce_xor$tests/simple/fiedler-cooley.v:27$4_Y
  end
  cell $sub $sub$tests/simple/fiedler-cooley.v:16$2
    parameter \A_SIGNED 0
    parameter \A_WIDTH 9
    parameter \B_SIGNED 0
    parameter \B_WIDTH 3
    parameter \Y_WIDTH 10
    connect \A \count_out
    connect \B 3'101
    connect \Y $sub$tests/simple/fiedler-cooley.v:16$2_Y
  end
  process $proc$tests/simple/fiedler-cooley.v:14$1
    assign { } { }
    assign { } { }
    assign { } { }
    assign { } { }
    assign { } { }
    assign { } { }
    assign { } { }
    assign $0\cnt_dn[9:0] $sub$tests/simple/fiedler-cooley.v:16$2_Y
    assign $0\cnt_up[9:0] $add$tests/simple/fiedler-cooley.v:17$3_Y
    assign $0\count_nxt[8:0] $1\count_nxt[8:0]
    assign $0\parity_out[0:0] $reduce_xor$tests/simple/fiedler-cooley.v:27$4_Y
    assign $0\carry_out[0:0] $and$tests/simple/fiedler-cooley.v:28$5_Y
    assign $0\borrow_out[0:0] $and$tests/simple/fiedler-cooley.v:29$6_Y
    assign $0\count_out[8:0] $1\count_nxt[8:0]
    switch { \up \down }
      case 2'00
        assign { } { }
        assign $1\count_nxt[8:0] \data_in
      case 2'01
        assign { } { }
        assign $1\count_nxt[8:0] $sub$tests/simple/fiedler-cooley.v:16$2_Y [8:0]
      case 2'10
        assign { } { }
        assign $1\count_nxt[8:0] $add$tests/simple/fiedler-cooley.v:17$3_Y [8:0]
      case 2'11
        assign { } { }
        assign $1\count_nxt[8:0] \count_out
      case
        assign { } { }
        assign $1\count_nxt[8:0] 9'xxxxxxxxx
    end
    sync posedge \clock
      update \count_out $0\count_out[8:0]
      update \carry_out $0\carry_out[0:0]
      update \borrow_out $0\borrow_out[0:0]
      update \parity_out $0\parity_out[0:0]
      update \cnt_up $0\cnt_up[9:0]
      update \cnt_dn $0\cnt_dn[9:0]
      update \count_nxt $0\count_nxt[8:0]
  end
end
