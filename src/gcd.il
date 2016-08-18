module \GCD
  wire output 5 \v
  wire width 17 \INFER_2
  wire width 16 \GEN_0
  wire width 16 \GEN_3
  wire input 3 \reset
  wire width 16 \GEN_1
  wire width 16 \GEN_2
  wire output 4 width 16 \z
  wire width 16 \x
  wire width 16 \y
  wire width 17 \INFER_1
  wire \T_20
  wire input 1 \e
  wire input 2 \clk
  wire width 16 \T_18
  wire \T_17
  wire input 6 width 16 \a
  wire width 16 \T_19
  wire input 7 width 16 \b
  cell $gt \CELL_1
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \Y_WIDTH 1
    connect \A \x
    connect \B \y
    connect \Y \T_17
  end
  cell $sub \CELL_2
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \Y_WIDTH 17
    connect \A \x
    connect \B \y
    connect \Y \INFER_1
  end
  cell $tail \CELL_3
    parameter \A_SIGNED 1
    parameter \A_WIDTH 17
    parameter \Y_WIDTH 16
    connect \A \INFER_1
    connect \Y \T_18
  end
  cell $sub \CELL_4
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \Y_WIDTH 17
    connect \A \y
    connect \B \x
    connect \Y \INFER_2
  end
  cell $tail \CELL_5
    parameter \A_SIGNED 1
    parameter \A_WIDTH 17
    parameter \Y_WIDTH 16
    connect \A \INFER_2
    connect \Y \T_19
  end
  cell $mux \CELL_6
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \S_SIGNED 0
    parameter \S_WIDTH 1
    parameter \Y_WIDTH 16
    connect \A \T_18
    connect \B \x
    connect \S \T_17
    connect \Y \GEN_0
  end
  cell $mux \CELL_7
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \S_SIGNED 0
    parameter \S_WIDTH 1
    parameter \Y_WIDTH 16
    connect \A \y
    connect \B \T_19
    connect \S \T_17
    connect \Y \GEN_1
  end
  cell $mux \CELL_8
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \S_SIGNED 0
    parameter \S_WIDTH 1
    parameter \Y_WIDTH 16
    connect \A \a
    connect \B \GEN_0
    connect \S \e
    connect \Y \GEN_2
  end
  cell $mux \CELL_9
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 16
    parameter \S_SIGNED 0
    parameter \S_WIDTH 1
    parameter \Y_WIDTH 16
    connect \A \b
    connect \B \GEN_1
    connect \S \e
    connect \Y \GEN_3
  end
  cell $eq \CELL_10
    parameter \A_SIGNED 0
    parameter \A_WIDTH 16
    parameter \B_SIGNED 0
    parameter \B_WIDTH 1
    parameter \Y_WIDTH 1
    connect \A \y
    connect \B 0
    connect \Y \T_20
  end
  connect \z \x
  connect \v \T_20
  connect \x \GEN_2
  connect \y \GEN_3
end
