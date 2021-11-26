GetRandomNum(min, max, method:="Int"){
    if (method="Int") {
        Random, output, ceil(min), floor(max)
    } else {
        Random, output, min*1.0, max*1.0
    }
    Return output
}