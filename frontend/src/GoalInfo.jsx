// GoalInfo.js
import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import './App.css';

const GoalInfo = ({ goalScorerHome, goalScorerAway, goalMinute, goalScore }) => {
  const [showVideoModal, setShowVideoModal] = useState(false);

  const handleShowVideoModal = () => {
    setShowVideoModal(true);
  };

  const handleCloseVideoModal = () => {
    setShowVideoModal(false);
  };

  // Replace the videoURL with the actual URL of your video
  const videoURL = 'https://www.youtube.com/embed/HquPOdaykrE';

  return (
    <>
      <div className="goal-info match-entry pt-4 pb-4" onClick={handleShowVideoModal}>
        <div className="col-md-4 col-lg-4 mb-4 mb-lg-0">
          <div className="text-center text-lg-left">
            {goalScorerHome && <span className="goal-minute">{goalScorerHome} {goalMinute}</span>}
          </div>
        </div>
        <div className="col-md-4 col-lg-4 mb-4 mb-lg-0">
          <div className="text-center text-lg-left">
            <div>
              <span className="goal-score">{goalScore}</span>
              <br />
              {/*<a href="#" className="mt-2" onClick={handleShowVideoModal}>*/}
              {/*  Watch the goal*/}
              {/*</a>*/}
            </div>
          </div>
        </div>
        <div className="col-md-4 col-lg-4 mb-4 mb-lg-0">
          <div className="text-center text-lg-left">
            {goalScorerAway && <span className="goal-minute">{goalScorerAway} {goalMinute}</span>}
          </div>
        </div>
      </div>

      <Modal show={showVideoModal} onHide={handleCloseVideoModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Goal Video</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {/* Embed the video player */}
          <iframe width="100%" height="400" src={videoURL}
                  title="Benzema Goal vs Switzerland | Euro 2020" frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen></iframe>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseVideoModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default GoalInfo;
