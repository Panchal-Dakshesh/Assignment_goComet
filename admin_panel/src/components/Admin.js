import React, {Component} from 'react';
import { Modal, Button } from "react-bootstrap";
import 'react-toastify/dist/ReactToastify.css';
import Notifications, {notify} from 'react-notify-toast';

export default class Admin extends Component {

    constructor(props) {
        super(props);

        // hold everything that we'll need throughout the application
        this.state = {
            search_results: ["Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending..."],
            search_history: [],
            tag: null,
            search: "",
            show: 'show',
            timer: null,
            searchResTimer: null,
            isModalOpen: false,
            currentBlog: null,
            currentTitle: null,
            currentAuthor: null,
            currentRead: null,
            currentUrl: null,
            currentTag: null,
            currentTimeTaken: null,
            currentComment: null,
            isSearchHistoryOpen: false,
            relatedTags: [],
        }
    }

    componentDidMount() {
        this.divstatus() // hides the result set initially
        this.fetchSearchResults(false, null) // fetches search history from db
    }

    // toggles between search results hide and show
    divstatus = (e) =>{

        if(this.state.search !== "") {
            this.setState({show: 'show'});
        }
        else {
            this.setState({show: 'hide'});
        }
    }

    // fetches search history from db
    fetchSearchResults(status, query) {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Accept", "application/json");

        var requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
        };

        fetch("http://127.0.0.1:5000/get-search-results", requestOptions)
        .then(response => response.text())
        .then(result => {
            result = JSON.parse(result);
            const search_history = this.state.search_history;
            if(search_history.length) {
                // console.log(search_history[0]);
                if(search_history[0][1] === result.data[0][1]) {
                    console.log("Match found!");
                    clearInterval(this.state.searchResTimer);
                }
            }
            else {
                result.data.reverse();
                result.data.map((element, index) => {
                    if(element[3] == 0 && status && element[1].toLowerCase() == query.toLowerCase()) {
                        // alert("Result not found for " + element[1] + ", showing search for popular tags");
                        notify.show("Result not found for " + element[1] + ", showing search for popular tags", 'error');
                    }
                    this.setState({ search_history: [...this.state.search_history, element] })
                })
            }
        })
        .catch(error => console.log('error', error));
    }

    // fetches crawler result from db after an interval
    onlyFetchResults() {
        
        // check if search result length is 10 and stop interval
        const timer = this.state.timer;
        const search_results = [...this.state.search_results];
        if(search_results.length >= 10 && search_results[9] !== "Pending...") {
            console.log("--- Timer cleared ---")
            clearInterval(timer);
            this.setState({ timer: null });
        }
        else {
            this.divstatus();
            // call server to fetch results from db
            var myHeaders = new Headers();
            myHeaders.append("Content-Type", "application/json");

            var requestOptions = {
            method: 'GET',
            headers: myHeaders,
            redirect: 'follow'
            };

            // calls the api to fetch blogs
            fetch("http://127.0.0.1:5000/get-blogs", requestOptions)
            .then(response => response.text())
            .then(result => {
                const res = JSON.parse(result);
                res.data.map((element, index) => {
                    const currentTag = element[4]
                    this.setState({ tag: currentTag });
                    // updates blog result in real-time
                    this.state.search_results[index] = element; 
                    if(index < 8) {
                        this.state.search_results[index + 1] = "Crawling...";
                    }
                    this.divstatus();
                })
                
                // populate related tags array
                res.tags.map((element, index) => {
                    this.state.relatedTags[index] = element[1];
                })
                
                // get unique tags
                let unique = [...new Set(this.state.relatedTags)];
                this.setState({ relatedTags: unique });
            })
            .catch(error => console.log('error', error));
        }
    }

    // fetches related tags from db 
    getRelatedTags() {
        // call server to fetch results from db
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        var requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
        };

        fetch("http://127.0.0.1:5000/get-related-tags", requestOptions)
        .then(response => response.text())
        .then(result => {
            const res = JSON.parse(result);
            let relatedTags = this.state.relatedTags;
            this.setState({ relatedTags: [] });
            res.tags.map((element, index) => {
                this.setState({ relatedTags: [...relatedTags, element[1]] });
            })
            console.log(relatedTags)
        })
        .catch(error => console.log('error', error));
    }

    // sends the user query to backend to crawl
    searchTag(tag) {
        // query the backend with tag
        let query = this.state.search
        if(tag) {
            query = tag;
        }
        else {
            query = query.trim().toLowerCase()
        }
        if(!query) {
            // alert("Please enter a tag!");
            notify.show("Please enter a tag!", 'error');
        }
        else {
            console.log("You searched for: "+ query);
            this.setState({ 
                search_results: ["Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending...","Pending..."], 
                search: query,
                // show: false,
                relatedTags: []
            })

            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag: query })
            };
            // calls API
            fetch('http://127.0.0.1:5000/search', requestOptions)
                .then(response => response.json())
                .then(data => console.log(data));
    
            // set event to call fetch result every 10 secs
            const timer = setInterval(() => {
                console.log('Polling server for results');
                this.onlyFetchResults()
            }, 2500);

            const search_res_timer = setInterval(() => {
                this.fetchSearchResults(true, query)
            }, 5000);

            this.setState({ search_history: [] });
            this.setState({ timer: timer, tag: query, searchResTimer: search_res_timer });
        }
    }   

    // updates the search state as user types in the query
    handleEvent = event => {
        this.setState({ search: event.target.value });
    }

    // sets the modal content after every click
    showDetails(index) {
        const blog = this.state.search_results[index];
        this.setState({ 
            currentTitle: blog[1],
            currentAuthor: blog[2],
            currentRead: blog[3],
            currentTag: blog[4],
            currentBlog: blog[5],
            currentComment: "Not available",
            currentUrl: blog[8],
            currentTimeTaken: blog[9], 
            isModalOpen: true,
        });
    }

    // hides blog modal
    hideModal = () => {
        this.setState({isModalOpen: false});
    }
    
    // hides search modal
    hideSearchModal = () => {
        this.setState({isSearchHistoryOpen: false});
    }

    // opens search modal onclick
    showSearchHistory() {
        this.setState({isSearchHistoryOpen: true});
    }

    // search for related tags found in blog modal
    handleTagsSearch(tag) {
        console.log("Tag to search: " + tag);
        clearInterval(this.state.timer);
        this.setState({isModalOpen: false});
        this.searchTag(tag)
        notify.show("Fetching results for tag: " + tag, 'success');
        // console.log(this.state);
    }


    // render results to page
    render() {

        return (
            <>
            <Notifications /> {/* Notifications JSX */}
            <div className="main">
            <span id="title">Medium Crawler</span> {/* App name */}
            <form className="main-search" onSubmit={(e) => {e.preventDefault(); this.searchTag()}}>
                <input onChange={this.handleEvent} className="inp" autoFocus type="text" autoComplete="off" placeholder="Input a tag to search medium" name="search" id="search" />
                <button type="submit" className="btn btn-outline-success">
                    <i className="fa fa-search"></i>
                </button>
            </form>
            <h2 className="text-center mt-5 search-results" hidden={this.state.tag ? false : true}>Results for <span style={{textDecoration: "underline"}}>"{this.state.tag}"</span> will appear below</h2>
            </div>
            <div className="count" onClick={() => {this.showSearchHistory()}}>
                <span className="search-history-count">
                    <i className="fa fa-history" id="history-icon"></i>
                    {this.state.search_history.length}
                </span>
            </div>
            <div id={this.state.show} className="content">
                <ol className="blogs">
                    {
                        this.state.search_results.map((result, index) => (
                            <li key={index} className="blog" onClick={() => this.showDetails(index)}>
                                {( (result[1] === "e" || result[1] === "r") ? result : result[1])}
                            </li>
                        ))
                    }
                </ol>
            </div>
            {/* blog modal */}
            <Modal show={this.state.isModalOpen} onHide={this.hideModal} dialogClassName="modal-lg">
                <Modal.Header closeButton>
                    <Modal.Title>Blog details</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {
                        <>
                            <span>
                                <h5 className="current-title">Title: {this.state.currentTitle}</h5>
                                <h6 className="current-author">Author: {this.state.currentAuthor}</h6>
                                <p className="read-time">{this.state.currentRead}</p>
                            </span>
                            <p className="current-blog">
                                {this.state.currentBlog}
                            </p>
                            <p className="source-url">Source url: <a href={this.state.currentUrl} target="_blank" rel="noreferrer">Medium</a></p>
                            <p>
                                Tags: <span>
                                    {
                                        (this.state.relatedTags).map((element, index) => (
                                            <>
                                                <span className="tags" key={index} onClick={() => this.handleTagsSearch(element)}> {element} </span>
                                                <span className="space-between" />
                                            </>
                                        ))
                                    }
                                </span>
                            </p>
                            <p className="float-left scraping-time">Time taken to scrape: {this.state.currentTimeTaken} secs</p>
                        </>
                    }
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={this.hideModal}>
                        Close
                    </Button>
                </Modal.Footer>
            </Modal>
            {/* search history modal */}
            <Modal show={this.state.isSearchHistoryOpen} onHide={this.hideSearchModal} dialogClassName="modal-dialog">
                <Modal.Header closeButton>
                    <Modal.Title>Search history</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {
                        this.state.search_history.map((result, index) => (
                            <ul key={result[0]}>
                                <li>
                                    <span className="search-history">{result[1].toUpperCase()}</span> searched at {result[2]}
                                </li>
                            </ul>
                        ))
                    }
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={this.hideSearchModal}>
                        Close
                    </Button>
                </Modal.Footer>
            </Modal>
            </>
        );
    }
}