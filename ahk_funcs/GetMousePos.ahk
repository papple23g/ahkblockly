GetMousePos(x_or_y, origin:="Screen"){
    CoordMode, Mouse , %origin%
    MouseGetPos, OutputVarX, OutputVarY
    if (x_or_y="x") {
        Return OutputVarX
    }
    Return OutputVarY
}