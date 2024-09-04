import { useEffect, useState } from 'react';

const SolarDisplay = () => {
    const [plot1Url, setPlot1Url] = useState('');
    const [plot2Url, setPlot2Url] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('http://localhost:5000/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            setPlot1Url(data.plot1_url);
            setPlot2Url(data.plot2_url);
        })
        .catch((error) => {
            console.error('Error:', error);
            setError('Failed to load solar data');
        });
    }, []);

    return (
        <div className="flex min-h-screen flex-col items-center">
            <p className="font-Ocean text-white mt-10">Solar Info for Lubbock Texas</p>
            <p className='items-center text-white text-xs'>Note: This is just an example.</p>
            {error && <p>{error}</p>}
            {!error && (
                <div className="flex flex-row justify-between">
                    <div className="w-1/2 p-4">
                        <h2>Plot 1: Relative Efficiency vs Irradiance</h2>
                        <img className="rounded-3xl w-full h-auto" id="plot1" src={plot1Url} alt="Plot 1" />
                    </div>
                    <div className="w-1/2 p-4">
                        <h2>Plot 2: Array Power vs Irradiance</h2>
                        <img className="rounded-3xl w-full h-auto" id="plot2" src={plot2Url} alt="Plot 2" />
                    </div>
                </div>
            )}
        </div>
    );
}

export default SolarDisplay;
