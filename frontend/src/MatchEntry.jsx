import React, {useEffect, useState} from 'react';
import { Modal, Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import GoalInfo from "./GoalInfo";
import axios from "axios";



const MatchEntry = ({matchId, team1, country1, score, team2, country2, img1, img2 }) => {
  const [showModal, setShowModal] = useState(false);
  const [goals, setGoals] = useState([]);


  const handleShowModal = () => {
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  useEffect(() => {
    // Fetch goals from the backend when the component mounts
   axios.get(`http://127.0.0.1:5000/goals?matchId=${matchId}`)
  // Replace with your actual backend endpoint
      .then(response => {
        setGoals(response.data);
      })
      .catch(error => {
        console.error("Error fetching goals:", error);
      });
  }, []);


  return (
    <>
      <div className="row bg-white align-items-center ml-0 mr-0 py-4 match-entry" onClick={handleShowModal}>
        <div className="col-md-4 col-lg-4 mb-4 mb-lg-0">
          <div className="text-center text-lg-left">
            <div className="d-block d-lg-flex align-items-center">
              <div className="image image-small text-center mb-3 mb-lg-0 mr-lg-3">
                {/*<img src={img1} alt="Team 1" className="img-fluid" />*/}
              </div>
              <div className="text w-100">
                <h3 className="h5 mb-0 text-black">{team1}</h3>
                <span className="text-uppercase small country">{country1}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4 col-lg-4 text-center mb-4 mb-lg-0">
          <div className="d-inline-block">
            <div className="bg-black py-2 px-4 mb-2 text-white d-inline-block rounded">
              <span className="h5">{score}</span>
            </div>
          </div>
        </div>
        <div className="col-md-4 col-lg-4 text-center text-lg-right">
          <div className="">
            <div className="d-block d-lg-flex align-items-center">
              <div className="image image-small ml-lg-3 mb-3 mb-lg-0 order-2">
                {/*<img src={img2} alt="Team 2" className="img-fluid" />*/}
              </div>
              <div className="text order-1 w-100">
                <h3 className="h5 mb-0 text-black">{team2}</h3>
                <span className="text-uppercase small country">{country2}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Game Details</Modal.Title>
        </Modal.Header>
        <Modal.Body className="custom-modal-body">
          <div className="row bg-white align-items-center ml-0 mr-0 py-4">
            <div className="col-md-4 col-lg-4 mb-4 mb-lg-0">
              <div className="text-center text-lg-left">
                <div className="d-block d-lg-flex align-items-center">
                  <div className="image image-small text-center mb-3 mb-lg-0 mr-lg-3">
                    {/*<img src={img1} alt="Team 1" className="img-fluid"/>*/}
                  </div>
                  <div className="text w-100">
                    <h3 className="h5 mb-0 text-black">{team1}</h3>
                    <span className="text-uppercase small country">{country1}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-4 col-lg-4 text-center mb-4 mb-lg-0">
              <div className="d-inline-block">
                <div className="bg-black py-2 px-4 mb-2 text-white d-inline-block rounded">
                  <span className="h5">{score}</span>
                </div>
              </div>
            </div>
            <div className="col-md-4 col-lg-4 text-center text-lg-right">
              <div className="">
                <div className="d-block d-lg-flex align-items-center">
                  <div className="image image-small ml-lg-3 mb-3 mb-lg-0 order-2">
                    {/*<img src={img2} alt="Team 2" className="img-fluid"/>*/}
                  </div>
                  <div className="text order-1 w-100">
                    <h3 className="h5 mb-0 text-black">{team2}</h3>
                    <span className="text-uppercase small country">{country2}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="row mt-4 bg-white align-items-center ml-0 mr-0 py-4">
            <div className="col-12">
              {/* Example Goal Data */}
              {goals.map((goal, index) => (
                <GoalInfo
                  key={index}
                  goalScorerHome={goal.goalScorerHome}
                  goalScorerAway={goal.goalScorerAway}
                  goalMinute={goal.goalMinute}
                  goalScore={goal.match_score}
                  goalVideo={goal.match_url}
                />
              ))}
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default MatchEntry;
