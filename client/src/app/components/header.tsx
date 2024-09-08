'use client'
import { SERVER_API_URL } from "../config";
import { useEffect, useState } from "react";
import Spreadsheet, { CellBase, Matrix, Point,  } from "react-spreadsheet";

interface ResponseData {
  msg: string;
}

type Cell = {
  row: number;
  column: number;
  value: string;
}

type Translation = {
  src: string;
  dst: string;
}

const columnLabels = ["S_TC", "E_TC", "SRC", "DST"]

export default function Header() {

  const [data, setData] = useState<Matrix<CellBase>>([
     [{value: "Paste your content"}], [], [], [], [], [], [], [], [], []
  ]);

 
// onCellCommit?: (prevCell: null | CellType, nextCell: null | CellType, coords: null | Point) => void;
  const handleCellCommit =  (prevCell: null | CellBase, nextCell: null | CellBase, coords: null | Point) => {
    if(!coords || !nextCell) return;
    console.log(`changed cell text from ${prevCell?.value} to ${nextCell.value} at row ${coords.row} and column ${coords.column}`);
    //console.log('data', data);
  }

  const handleChange = (newData: Matrix<CellBase>) => {
    console.log('matrix', newData, data);
    // compare the matrix with the data and generate array of coords with changed values
    let changedCells: Cell[] = [];
    newData.forEach((row, rowIndex) => {
      row.forEach((col, colIndex) => {
        if(!data[rowIndex]) {
          changedCells.push({row: rowIndex, column: colIndex, value: col?.value || ""});
        }
        else if((data[rowIndex][colIndex] === undefined || data[rowIndex][colIndex].value === undefined)
          && col && col.value !== undefined) {
            changedCells.push({row: rowIndex, column: colIndex, value: col.value});
          }
        else if(data[rowIndex][colIndex] && col && data[rowIndex][colIndex].value !== col.value) {
          changedCells.push({row: rowIndex, column: colIndex, value: col.value});
        }  
    })
  })
  console.log('changedCells', changedCells)
   
    setData(newData);   
  }

  

  const makeRequest = async (data: string, context: Translation[]) => {
    const response = await fetch(SERVER_API_URL+"/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({data, context})
    });
    const translatedData = await response.json();
    console.log('translatedData', translatedData);
  }

    
  const contextWindowLength = 10;
  const handleTranslate = async () => {
    console.log('translating');
    // handle translation by sending one row at a time from data
    let contextWindow: Translation[] = [];
    data.forEach(async (row: any, i: number) => {
      if(!row[2]?.value) return; // if source is empty, skip
      const src = row[2]?.value;
      const dst = row[3]?.value || "";
      
      contextWindow.push({src, dst});
      await makeRequest(dst, contextWindow.slice(0, contextWindow.length - 1))
      if(contextWindow.length >= contextWindowLength) {
        // remove the first element
        contextWindow.shift();
      }
      // console.log(`contextWindow for row ${i}`, contextWindow);
    })
  }

  return (
    <div>
       <main className="container">
        <button onClick={() => handleTranslate()}>Translate All</button>
        <br></br>
      <Spreadsheet
        data={data}
        columnLabels={columnLabels}
        rowLabels={[]}
        onChange={handleChange}
        onCellCommit={handleCellCommit}
      />
        </main>
    </div>
  );
}
