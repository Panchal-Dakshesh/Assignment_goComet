import React from 'react';
import {Button, Modal} from 'react-bootstrap';
const BlogModal = (props) => {
    console.log(props);
    return (
        <Modal show={props.isModalOpen} onHide={props.closeCartModal} dialogClassName="cartModal modal-lg">
            <Modal.Header closeButton>
                <Modal.Title>Blog details</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {
                    <>
                        <span>
                            <h5>Title: {props.title}</h5>
                            <h6>Author: {props.author}</h6>
                            <p>{props.read}</p>
                        </span>
                        <p>
                            {props.blog}
                        </p>
                        <p>Source url: <a href={props.url}>Medium</a></p>
                        <p>
                            Tags: <span className="tags">{props.tags}</span>
                        </p>
                        <p className="float-left">Time taken to scrape: {props.time_taken} secs</p>
                    </>
                }
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={props.hideModal}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
 }
 export default BlogModal;