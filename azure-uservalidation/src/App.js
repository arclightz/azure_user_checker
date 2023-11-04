import React from 'react';
import FileUpload from './components/FileUpload';
import 'bootstrap/dist/css/bootstrap.css';
import { Container, Row, Col } from 'react-bootstrap';
import './App.css';

function App() {
  return (
    <div className="App-header">
    <Container>
      <Row className="mt-4">
        <Col md={6} className="mx-auto">
          <FileUpload />
        </Col>
      </Row>
    </Container>
    </div>
  );
}

export default App;
