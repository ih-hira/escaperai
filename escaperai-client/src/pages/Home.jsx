import { Box, Button, Container, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import escaperaiLogo from '../assets/escaper-ai-logo.svg';

const Home = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box 
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          py: 4,
        }}
      >
        <img 
          src={escaperaiLogo} 
          alt="EscaperAi Logo"
          style={{
            height: '200px',
            marginBottom: '2rem',
            display: 'block',
            margin: '0 auto 2rem auto'
          }}
        />
        <Typography 
          variant="h3" 
          component="h1"
          sx={{ 
            mb: 2, 
            textAlign: 'center',
            color: 'secondary.main'
          }}
        >
          Welcome to EscapperAi
        </Typography>
        <Typography 
          variant="body1"
          sx={{ 
            mb: 2, 
            textAlign: 'center',
            color: 'secondary.light'
          }}
        >
          Your next adventure begins here. Start planning unforgettable trips with our intuitive planning tools and make every journey memorable.
        </Typography>
        <Button 
          variant="contained" 
          size="large"
          onClick={() => navigate('/login')}
          sx={{ mt: 2 }}
        >
          Get Started
        </Button>
      </Box>
    </Container>
  );
};

export default Home;