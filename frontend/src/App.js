import './App.css';
import logo from "./images/logo.png";
import backgroundImage from "./images/hero_bg_3.jpg";
import img_1_sq from "./images/img_1_sq.jpg";
import 'bootstrap/dist/css/bootstrap.min.css';
import {useEffect, useState} from "react";
import MatchEntry from "./MatchEntry";
import axios from 'axios';


function App() {
        const [scrollPosition, setScrollPosition] = useState(0);
    const [matches, setMatches] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        axios.get("http://127.0.0.1:5000/matches")
            .then((response) => {
                const data = response.data;
                console.log(data);  // Log the data to inspect its structure

                if (Array.isArray(data)) {
                    setMatches(data);
                } else {
                    console.error("Invalid API response. Expected an array.");
                }

                setIsLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching matches:", error);
                setIsLoading(false);
            });
    }, []);


    console.log(matches);

    useEffect(() => {
        const handleScroll = () => {
            setScrollPosition(window.scrollY);
        };

        window.addEventListener('scroll', handleScroll);

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    if (isLoading) {
        return <p>Loading...</p>;
    }

    return (
        <div className="site-wrap">
            <div className="site-mobile-menu">
                <div className="site-mobile-menu-header">
                    <div className="site-mobile-menu-logo">
                        <a href="#"><img src={logo} alt="Image"/></a>
                    </div>
                    <div className="site-mobile-menu-close mt-3">
                        <span className="icon-close2 js-menu-toggle"></span>
                    </div>
                </div>
                <div className="site-mobile-menu-body"></div>
            </div>
            {/*Header*/}
            <header className="site-navbar absolute transparent" role="banner">
                <nav className="site-navigation position-relative text-right bg-black text-md-right" role="navigation">
                    <div className="container position-relative">
                        <div className="site-logo">
                            <a href="index.html"><img src={logo} alt=""/></a>
                        </div>

                        <div className="d-inline-block d-md-none ml-md-0 mr-auto py-3"><a href="#" className="site-menu-toggle js-menu-toggle text-white"><span
                            className="icon-menu h3"></span></a></div>
                    </div>
                </nav>
            </header>

            {/*Background Image*/}
            <div className="site-wrap">
                <div className="site-blocks-cover" style={{
                    backgroundImage: `url(${backgroundImage})`,
                    backgroundPositionY: `-${scrollPosition / 2}px`
                }}>
                    <div className="overlay"></div>
                    <div className="container">
                        <div className="row align-items-center justify-content-start">
                            <div className="col-md-6 text-center text-md-left" data-aos="fade-up" data-aos-delay="400">
                                <h1 className="bg-text-line">Match</h1>
                                <p className="mt-4">Here you can see all the live goals in the real time</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/*Matches*/}
            <div className="site-section site-blocks-vs">
                <div className="container">
                    <div className="row align-items-center mb-5">
                        <div className="col-md-12">

                            {matches.map((match) => {
                const { home_team_name, away_team_name, score_home, score_away , match_time, league_name} = match;

                const hasScores = score_home !== "" && score_away !== "";

                const score = hasScores ? `${score_home}:${score_away}` : `${match_time}`;

                return (
                  <MatchEntry
                    key={match.id}
                    matchId={match.id}
                    team1={home_team_name}
                    country1={league_name}
                    score={score}
                    team2={away_team_name}
                    country2=""
                    img1={img_1_sq}
                    img2={img_1_sq}
                  />
                );
              })}
                        </div>
                    </div>
                    {/*Pagination*/}
                    {/*<div className="row">*/}
                    {/*    <div className="col-md-12 text-center">*/}
                    {/*        <div className="site-block-27">*/}
                    {/*            <ul>*/}
                    {/*                <li><a href="#">&lt;</a></li>*/}
                    {/*                <li className="active"><span>1</span></li>*/}
                    {/*                <li><a href="#">2</a></li>*/}
                    {/*                <li><a href="#">3</a></li>*/}
                    {/*                <li><a href="#">4</a></li>*/}
                    {/*                <li><a href="#">5</a></li>*/}
                    {/*                <li><a href="#">&gt;</a></li>*/}
                    {/*            </ul>*/}
                    {/*        </div>*/}
                    {/*    </div>*/}
                    {/*</div>*/}
                </div>
            </div>
        </div>
    );
}

export default App;
