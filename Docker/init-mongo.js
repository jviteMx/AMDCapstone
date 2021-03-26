db.createUser(
    {
        user : "AMD",
        pwd : "UofC",
        roles : [{
            role : "readWrite",
            db : "AMDmongo"
        }
        ]
    }
)