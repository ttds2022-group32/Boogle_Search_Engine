import React from 'react';

const ip_address = "http://35.195.142.184/"

const Item = (props) => {
    return (
        <div className="p-2 bg-white shadow-lg rounded-md w-xxl">
            <div className="container grid grid-cols-5 shrink">
                <div className="w-full mx-auto col-span-1">
                    <img className="rounded-md" src={props.image} alt="" />
                </div>
                <div className="col-span-4">
                    <div className="text-xl font-bold text-black mb-2">
                        <a className="text-sky-800 hover:text-blue-800 visited:text-purple-600" href={ip_address + "book/?book_id=" + props.book}>{props.title}</a>
                    </div>
                    <ul>
                        <li>
                            <strong>Author: </strong>
                            {props.author.name}
                        </li>
                        <li>
                            <strong>Published Year: </strong>
                            {props.year}
                        </li>
                        <li>
                            <strong>Content: </strong>
                            {props.content}
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    )
}

export default Item;