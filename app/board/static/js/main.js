function getData() {
  $.ajax({
    type: "GET",
    url: "/chessapi/api/get_moveline?fen=" + $fen.html(),
    dataType: "json",
    error: function () {
      console.log("통신실패!!");
    },
    success: function (moves) {
      if (moves.msg) {
        $tableBody.empty();
        $tableBody.append(moves.msg);
        return;
      }
      moves = JSON.parse(moves);
      console.log(moves);
      $tableBody.empty();
      for (var i = 0; i < moves.length; i++) {
        var move = moves[i];
        var row = document.createElement("tr");
        var blackWinRateCell = document.createElement("td");
        blackWinRateCell.textContent = (
          move.fields.black /
          (move.fields.black + move.fields.white + move.fields.draw)
        ).toFixed(2);
        var cntCell = document.createElement("td");
        cntCell.textContent = move.fields.cnt;
        var drawRateCell = document.createElement("td");
        drawRateCell.textContent = (
          move.fields.draw /
          (move.fields.black + move.fields.white + move.fields.draw)
        ).toFixed(2);
        var nextMoveCell = document.createElement("td");
        nextMoveCell.textContent = move.fields.next_move;
        nextMoveCell.addEventListener("click", function (event) {
          let target = event.target;
          onDrop(
            target.textContent.slice(0, 2),
            target.textContent.slice(2, 4)
          );
          onSnapEnd();
        });
        var whiteWinRateCell = document.createElement("td");
        whiteWinRateCell.textContent = (
          move.fields.white /
          (move.fields.black + move.fields.white + move.fields.draw)
        ).toFixed(2);
        row.appendChild(nextMoveCell);
        row.appendChild(cntCell);
        row.appendChild(whiteWinRateCell);
        row.appendChild(drawRateCell);
        row.appendChild(blackWinRateCell);
        $tableBody.append(row);
      }
      $opening.html(moves.name);
    },
  });
}
function getStockFish() {
  if (!$uci.html()) {
    $stockfishBody.empty();
    return;
  }
  $.ajax({
    type: "GET",
    url: "/chessapi/api/stockfish?fen=" + $fen.html(),
    dataType: "json",
    error: function () {
      console.log("통신실패!!");
    },
    success: function (moves) {
      console.log(moves);
      $stockfishBody.empty();

      for (var i = 0; i < moves.length; i++) {
        var move = moves[i];
        var newRow = $(
          "<tr><td>" +
            move.Move +
            "</td><td>" +
            move.Centipawn +
            "</td><td>" +
            move.Mate +
            "</td></tr>"
        );
        newRow.click(function (event) {
          let target = event.target;
          onDrop(
            target.textContent.slice(0, 2),
            target.textContent.slice(2, 4)
          );
          onSnapEnd();
        });
        $stockfishBody.append(newRow);
      }
    },
  });
}

function getEval() {
  console.log($fen.html());
  $.ajax({
    type: "GET",
    url: "/chessapi/api/eval_position?fen=" + $fen.html(),
    dataType: "json",
    error: function () {
      console.log("통신실패!!");
    },
    success: function (data) {
      console.log(data);
    },
  });
}

