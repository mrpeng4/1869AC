// USE THIS TO PROTECT A PATH BY SURROUNDING IT
import { useNavigate} from 'react-router-dom';
export default function Protected({authenticated, page}){
    const Navigate = useNavigate()
    if(!authenticated){
        return <Navigate to = "/login"/>;
    }
    return page;
}