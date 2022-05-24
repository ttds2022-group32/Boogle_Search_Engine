import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Results from './Results';
import boogle from "./images/Boogle.jpg";
import logo from "./images/logo_pic.jpg";
import notfound from "./images/404.jpg";
import copyright404 from "./images/404_copyright.jpg"

/**
 * @function Search
 */




const Search = (props) => {
    const [searchTerms, setSearchTerms] = useState('')
    const [results, setResults] = useState()
    const [errors, setErrors] = useState()
    const [buttonPressed, setButtonPressed] = useState()
    const [author, setAuthor] = useState()

    const ip_address = "http://35.195.142.184/"

    const getAuthor = () => {
        axios
            .get(ip_address + "random_author")
            .then(response => {
                console.log(response)
                console.log("Data:" + response.data)
                setAuthor(response.data)
                // setSearchTerms(response.data[0])
            })
    }
    useEffect(getAuthor, [])

    const addSearch = (event) => {
        event.preventDefault()
        console.log('button clicked', searchTerms)
        setButtonPressed(true)
        setResults()
        axios
            .get(ip_address + "search/?query=" + searchTerms)
            .catch(function (error) {
                console.log("We managed to catch this error", error.message)
                setErrors(true)
            })
            .then(response => {
                console.log(response)
                console.log("Data:" + response.data)
                setResults(response.data)
            })

    }

    const solid_Search = (event) => {
        event.preventDefault()
        console.log('button clicked', searchTerms)
        setButtonPressed(true)
        setResults()
        axios
            .get(ip_address + "solid_search/?query=" + searchTerms)
            .catch(function (error) {
                console.log("We managed to catch this error", error.message)
                setErrors(true)
            })
            .then(response => {
                console.log(response)
                console.log("Data:" + response.data)
                setResults(response.data)
            })

    }


    const handleChange = (event) => {
        console.log(event.target.value)
        setSearchTerms(event.target.value)

    }

    var expand_query = results && results["expand"] ? results["expand"] : undefined
    var original_query = results && results["expand"] ? results["original"] : undefined
    console.log(expand_query)
    console.log(original_query)
    let change = results && results["expand"] && results["expand"] !== results["original"]
    if (errors) {
        return <div>
            <div className='flex flex-col justify-center items-center bg-gradient-to-r from-cyan-700'>
                <img src={notfound} alt="" width="600" />
            </div>
            <div className='flex flex-col justify-center items-center'>
                <div className='text-xl'><b>Please refresh the page or go back</b></div>
            </div>
            <div className="absolute bottom-0 left-0">
                <img src={copyright404} alt="" width="300" />
            </div>
        </div>
    }
    return (
        <div>
            <div className='flex flex-col justify-center items-center bg-gradient-to-r from-cyan-700'>
                <div className="flex">
                    <img src={boogle} alt="" width="100" />
                </div>
                <img src={logo} alt="" width="300" />
                <div className='flex justify-center items-center-top h-[150px]'>
                    <input value={searchTerms} onChange={handleChange} className='w-[480px] h-[50px] rounded-l-full shadow-lg shadow-zinc-300 outline-none
                        font-thin text-xl px-4' placeholder='quote; book name; author...'></input>
                    <button onClick={author ? solid_Search: addSearch} className='h-[50px] w-[100px] bg-sky-600 rounded-r-full text-xl font-bold
                        shadow-lg shadow-zinc-300 text-white hover:bg-sky-800'>Search</button>

                </div>
            </div>
            {author && !buttonPressed ? <Author author={author} getAuthor={getAuthor} setSearchTerms={setSearchTerms}/> : undefined}
            {!results && buttonPressed ? <Spinner /> : undefined}
            {change ? <div>
                <div className='text-xl'>Showing results for  <b>{results["expand"]}</b></div>
                <div>Search instead for <button className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600" onClick={solid_Search}>{results["original"]}</button></div>
            </div> : undefined
            }
            <Results results={results} />
        </div>
    )
}

const Spinner = () => {
    return (
        <div className="font-bold flex justify-center items-center text-[42px] m-20">
            < svg role="status" class="mr-2 w-20 h-20 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg" >
                <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
            </svg >
        </div>
    )
}

const Author = ({ author, getAuthor,setSearchTerms }) => {
    return (
        <div class="flex-col justify-center items-center m-5 p-4 text-gray-800 bg-white rounded-lg shadow">
            <div class="mb-2">
                <div class="h-3 text-5xl text-left text-gray-600">“</div>
                <p class="px-4 text-xl text-center text-gray-600 mx-5">
                    Try searching for <button onClick={() => {setSearchTerms(author[0])}} target="_blank" className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600">{author[0]}</button> 
                    ; or know more on <a href={author[1]} target="_blank" className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600">wikipedia</a>
                </p>

                <div class="h-3 text-5xl text-right text-gray-600">”</div>

            </div>
            <div class="flex justify-center items-center">
                <button onClick={getAuthor} class="bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow">
                    I'm feeling lucky
                </button>
            </div>

        </div>

    )
}

export default Search