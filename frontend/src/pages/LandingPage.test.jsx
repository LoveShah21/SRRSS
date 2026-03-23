import { render, screen } from '@testing-library/react';
import LandingPage from './LandingPage';

describe('LandingPage', () => {
  it('renders SRRSS heading', () => {
    render(<LandingPage />);
    expect(screen.getByText(/Smart Recruitment & Resume Screening System/i)).toBeInTheDocument();
  });
});
