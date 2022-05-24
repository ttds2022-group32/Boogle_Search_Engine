import List from './List'
import copyright from "./images/copyright.jpg"

const Results = ({results}) => {
    if (!results){
        return <h1 className="font-bold flex justify-center items-center text-[42px]"> </h1>
    }else if (results === "None"){
        return (
            <div>
                <h1 className="font-bold flex justify-center items-center text-[42px]">No Match!</h1>
                <h1 className="font-normal flex justify-center items-center text-[21px]">Please check the search item and search again</h1>
            </div>
        )
    }else {
        return (<div>
            <List results={results}/>
            <div className="flex bottom-0 left-0">
                <img src={copyright} alt = "" width="200"/>
            </div>
        </div>
        
        )
        
    }
    
}

export default Results