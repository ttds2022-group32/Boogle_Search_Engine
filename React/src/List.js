import Item from './Item'

import React, { useState } from 'react';

/**
 * @function List
 */

const List = (props) => {

  const data = props.results  
  var booklist = []
  for (var d in data) {
    booklist.push(data[d])
  }


  //console.log(booklist)

  return (
    <div className="container mx-auto">
      <div className="flex flex-col gap-y-3">
        {booklist.filter(book=>(book._id)).map(book=>(
          <Item key={book._id} book={book.book_id} title={book.title} year={book.year} author={book.author} content={book.content} image={book.image_src}/>
        ))}
      </div>
    </div>
  )
}

export default List;
