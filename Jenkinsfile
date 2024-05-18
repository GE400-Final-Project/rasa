pipeline {
    agent any

    stages {	    
        stage('Build') {
            steps {     
		    
		   sh '''
		       cd /home/rasa/rasa
        	   #git reset --hard HEAD^
	           git pull https://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@github.com/GE400-Final-Project/rasa.git main
        	   '''      
	           sh "chmod -R 755 /usr/local/bin"
            }
        }
        stage('Deploy') {
            steps {                                     
                    sh "pwd"                                 
         	       sh "docker-compose -f /home/rasa/rasa/rasa-app-data/docker-compose.yml down"
                    sh "docker-compose -f /home/rasa/rasa/rasa-app-data/docker-compose.yml up -d"			
                    sh "chmod -R 1000 /usr/local/bin"
            }
        }
        stage('End') {
            steps {
                echo 'Success'
            }
        }
    }
}