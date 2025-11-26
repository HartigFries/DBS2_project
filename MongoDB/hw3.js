try {

    db.users.insertMany([
        { _id: 9001, username: "Aragorn", country: "cz", join_date: ISODate("2022-11-15T10:00:00Z"), joined_groups: [{ group_id: 9001, joined_at: ISODate("2022-11-16T10:00:00Z") }], created_posts: [9001], is_commercial: 1 },
        { _id: 9002, username: "Boromir", country: "us", join_date: ISODate("2022-12-05T10:00:00Z"), joined_groups: [{ group_id: 9002, joined_at: ISODate("2022-12-06T10:00:00Z") }], created_posts: [9002], is_commercial: 0 },
        { _id: 9003, username: "Smíšek", country: "de", join_date: ISODate("2022-10-05T14:30:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9004, username: "Sam", country: "pl", join_date: ISODate("2021-05-20T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9005, username: "Pipin", country: "cz", join_date: ISODate("2021-06-10T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9006, username: "Frodo", country: "us", join_date: ISODate("2021-07-01T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9007, username: "Gandalf", country: "de", join_date: ISODate("2021-08-15T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9008, username: "Uriel", country: "pl", join_date: ISODate("2021-09-10T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9009, username: "Gabriel", country: "cz", join_date: ISODate("2021-10-05T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9010, username: "Izák", country: "cz", join_date: ISODate("2021-11-01T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9011, username: "Abrahám", country: "us", join_date: ISODate("2021-12-20T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 },
        { _id: 9012, username: "Čestmír", country: "us", join_date: ISODate("2022-01-10T00:00:00Z"), joined_groups: [], created_posts: [], is_commercial: 0 }
    ]);

    db.groups.insertMany([
        { _id: 9001, name: "Dead Group", country: "cz", posts: [9001], last_activity: ISODate("2022-10-01T00:00:00Z") },
        { _id: 9002, name: "Active Group", country: "us", posts: [9002], last_activity: ISODate("2022-12-25T00:00:00Z") },
        { _id: 9003, name: "Photo Club", country: "uk", posts: [], last_activity: ISODate("2022-11-01T00:00:00Z") },
        { _id: 9004, name: "Cooking", country: "fr", posts: [], last_activity: ISODate("2022-12-15T00:00:00Z") },
        { _id: 9005, name: "Tech", country: "us", posts: [], last_activity: ISODate("2022-09-01T00:00:00Z") },
        { _id: 9006, name: "Gaming", country: "cz", posts: [], last_activity: ISODate("2022-12-30T00:00:00Z") }
    ]);

    db.activities.insertMany([
        { _id: 50, region: "Sumava", country: "cz", distance_m: 15000, base_elev_m: 200, total_elev_m: 500 },
        { _id: 9002, region: "Grand Canyon", country: "us", distance_m: 10000, base_elev_m: 1000, total_elev_m: 2000 },
        { _id: 9003, region: "Alps", country: "de", distance_m: 20000, base_elev_m: 1500, total_elev_m: 3000 },
        { _id: 9004, region: "Tatras", country: "pl", distance_m: 12000, base_elev_m: 900, total_elev_m: 1500 },
        { _id: 9005, region: "Rockies", country: "us", distance_m: 25000, base_elev_m: 1200, total_elev_m: 2500 },
        { _id: 9006, region: "Beskydy", country: "cz", distance_m: 8000, base_elev_m: 400, total_elev_m: 800 }
    ]);

    db.posts.insertMany([
        { _id: 9001, text: "October Post", created_at: ISODate("2022-10-15T14:00:00Z"), tags: [9002], group: 9001, user: 9001, activity: 50 },
        { _id: 9002, text: "December Post", created_at: ISODate("2022-12-05T09:00:00Z"), tags: [9001], group: 9002, user: 9002, activity: 9002 },
        { _id: 9003, text: "Task 12 Post", created_at: ISODate("2022-11-01T10:00:00Z"), tags: [], group: null, user: 9001, activity: ObjectId("000000000000000000000032") },
        { _id: 9004, text: "Hello World", created_at: ISODate("2022-09-01T10:00:00Z"), tags: [], group: null, user: 9004, activity: null },
        { _id: 9005, text: "Nice view", created_at: ISODate("2022-09-05T12:00:00Z"), tags: [], group: 99003, user: 9005, activity: 99003 },
        { _id: 9006, text: "Running", created_at: ISODate("2022-10-01T08:00:00Z"), tags: [], group: null, user: 9006, activity: null },
        { _id: 9007, text: "Hike", created_at: ISODate("2022-11-01T15:00:00Z"), tags: [9001], group: 9001, user: 9001, activity: 50 },
        { _id: 9008, text: "Winter", created_at: ISODate("2022-12-01T09:00:00Z"), tags: [], group: null, user: 9007, activity: null },
        { _id: 9009, text: "Wedding", created_at: ISODate("2022-10-20T10:00:00Z"), tags: [9003], group: null, user: 9002, activity: null },
        { _id: 9010, text: "Horse riding", created_at: ISODate("2022-12-10T11:00:00Z"), tags: [9004], group: 9002, user: 9003, activity: null }
    ]);

    db.comments.insertMany([
        { _id: 9001, user_id: 9003, post_id: 9001, written_at: ISODate("2022-10-16T10:00:00Z") },
        { _id: 9002, user_id: 9002, post_id: 9002, written_at: ISODate("2022-11-18T11:00:00Z") },
        { _id: 9003, user_id: 9001, post_id: 9003, written_at: ISODate("2022-12-06T09:00:00Z") },
        { _id: 9004, user_id: 9004, post_id: 9004, written_at: ISODate("2022-09-02T10:30:00Z") },
        { _id: 9005, user_id: 9005, post_id: 9005, written_at: ISODate("2022-09-06T12:30:00Z") },
        { _id: 9006, user_id: 9006, post_id: 9001, written_at: ISODate("2022-10-17T09:00:00Z") },
        { _id: 9007, user_id: 9007, post_id: 9002, written_at: ISODate("2022-11-19T15:00:00Z") },
        { _id: 9008, user_id: 9008, post_id: 9003, written_at: ISODate("2022-12-07T18:00:00Z") },
        { _id: 9009, user_id: 9009, post_id: 9009, written_at: ISODate("2022-10-21T11:00:00Z") },
        { _id: 9010, user_id: 9010, post_id: 9010, written_at: ISODate("2022-12-11T13:00:00Z") }
    ]);
} catch (e) {
    print("Sample data already exist (skipping insert)");
}
// ---------------------------------------------------------------------------------------------
// Task 1
// ---------------------------------------------------------------------------------------------
print("Task 1")

var startDate = ISODate("2022-12-31T23:59:59Z");

db.users.aggregate([
    {
        $lookup: {
            from: "post",
            localField: "created_posts.$oid",
            foreignField: "_id",
            as: "post_details"
        }
    },
    {
        $lookup: {
            from: "comment",
            localField: "writes_comments.$oid",
            foreignField: "_id",
            as: "comment_details"
        }
    },
    {
        $project: {
            _id: 0,
            user_id: "$_id",
            username: "$username",
            all_activities: {
                $concatArrays: [
                    "$joined_groups.joined_at", 
                    "$post_details.created_at",
                    "$comment_details.written_at" 
                ]
            }
        }
    },
    {
        $project: {
            user_id: "$user_id",
            username: "$username",
            latest_activity: { $max: "$all_activities"}
        }
    },
    {
        $match: {
            latest_activity: { $lte: startDate }
        }
    },
    {
        $project: {
            user_id: "$user_id",
            username: "$username",
            time_difference_ms: {
                $subtract: [
                    startDate,
                    "$latest_activity"
                ]
            }
        }
    },
    {
        $project: {
            user_id: "$user_id",
            username: "$username",
            days_inactive: {
                $round: [
                    { $divide: ["$time_difference_ms", 86400000] },
                    0 
                ]
            }
        }
    },

    { $sort: { days_inactive: -1 } }
]);

// ---------------------------------------------------------------------------------------------
// Task 2
// ---------------------------------------------------------------------------------------------
print("Task 2")

var startDate = ISODate("2022-12-31T23:59:59Z");

db.groups.aggregate([
    {
        $lookup: {
            from: "post",
            localField: "posts.$oid",
            foreignField: "_id",
            as: "recent_posts"
        }
    },
    {
        $addFields: {
            recent_posts: {
                $filter: {
                    input: "$recent_posts",
                    as: "post",
                    cond: { $gte: ["$$post.created_at", startDate] }
                }
            }
        }
    },
    {
        $project: {
            _id: 0,
            group_id: "$_id",
            group_name: "$name",
            posts_7_days: { $size: "$recent_posts" },
            member_count: 0 
        }
    },
    {
        $match: { posts_7_days: { $gt: 0 } }
    },
    {
        $lookup: {
            from: "user",
            pipeline: [
                {
                    $match: {
                        "joined_groups.group_id": "$$group_id"
                    }
                },
                { $count: "member_count" }
            ],
            as: "member_data",
            let: { group_id: "$group_id" }
        }
    },
    {
        $project: {
            group_id: "$group_id",
            group_name: "$group_name",
            posts_7_days: "$posts_7_days",
            member_count: { $ifNull: [{ $arrayElemAt: ["$member_data.member_count", 0] }, 0] }
        }
    },

    { $sort: { posts_7_days: -1 } },

    { $limit: 10 }
]);

// ---------------------------------------------------------------------------------------------
// Task 3
// ---------------------------------------------------------------------------------------------
print("Task 3")

var startDate = ISODate("2022-12-31T23:59:59Z");

db.users.aggregate([
    { $unwind: "$joined_groups" },

    {
        $match: {
            "joined_groups.joined_at": { $gte: startDate }
        }
    },
    {
        $group: {
            _id: "$joined_groups.group_id",
            new_member_count: { $sum: 1 }
        }
    },
    {
        $lookup: {
            from: "group",
            localField: "_id",
            foreignField: "_id",
            as: "group_info"
        }
    },
    {  $unwind: "$group_info" },

    { $sort: { new_member_count: -1 } },

    { $limit: 10 },

    {
        $project: {
            _id: 0,
            group_id: "$_id",
            group_name: "$group_info.name",
            new_member_count: "$new_member_count"
        }
    }
]);

// ---------------------------------------------------------------------------------------------
// Task 4
// ---------------------------------------------------------------------------------------------
print("Task 4")

var startOfMonth = ISODate("2022-12-31T00:00:00Z");
var endOfMonth = ISODate("2022-12-31T23:59:59Z");

db.post.aggregate([
    {
        $match: {
            "created_at": { 
                $gte: startOfMonth, 
                $lt: endOfMonth
            }
        }
    },
    {
        $lookup: {
            from: "activity",
            localField: "activity",
            foreignField: "_id",
            as: "activity_details"
        }
    },

    { $unwind: "$activity_details" },

    {
        $group: {
            _id: "$user_id",
            total_distance: { $sum: "$activity_details.distance_m" },
            total_steps: { $sum: "$activity_details.steps" }
        }
    },
    {
        $lookup: {
            from: "user",
            localField: "_id",
            foreignField: "_id",
            as: "user_info"
        }
    },
    { $unwind: "$user_info" },
    
    { $sort: { total_distance: -1 } },

    { $limit: 20 },
    
    {
        $project: {
            _id: 0,
            user_id: "$_id",
            username: "$user_info.username",
            total_distance: "$total_distance",
            total_steps: "$total_steps"
        }
    }
]);

// ---------------------------------------------------------------------------------------------
// Task 5
// ---------------------------------------------------------------------------------------------
print("Task 5")
var startOfMonth = ISODate("2022-12-31T00:00:00Z");
var endOfMonth = ISODate("2022-12-31T23:59:59Z");

db.post.aggregate([
    {
        $match: {
            "created_at": { 
                $gte: startOfMonth, 
                $lt: endOfMonth
            }
        }
    },
    {
        $lookup: {
            from: "activity",
            localField: "activity",
            foreignField: "_id",
            as: "activity_details"
        }
    },
    
    { $unwind: "$activity_details" },
    
    {
        $group: {
            _id: { 
                region: "$activity_details.region",
                month: { $month: "$created_at" }
            },
            total_post_count: { $sum: 1 } 
        }
    },
    {
        $sort: { 
            "_id.region": 1,
            "_id.month": 1
        }
    },
    {
        $project: {
            _id: 0,
            region: "$_id.region",
            month: "$_id.month",
            total_post_count: "$total_post_count"
        }
    }
]);

// ---------------------------------------------------------------------------------------------
// Task 6
// ---------------------------------------------------------------------------------------------
print("Task 6")
db.posts.aggregate([
    {
        $match: {
            created_at: { $gte: ISODate("2022-10-01T00:00:00Z") },
            tags: { $ne: [] }
        }
    },
    { $unwind: "$tags" },
    {
        $group: {
            _id: "$tags",              // tagged user (ObjectId)
            tagCount: { $sum: 1 }
        }
    },
    { $sort: { tagCount: -1 } },
    { $limit: 10 },
    {
        $lookup: {
            from: "users",
            localField: "_id",         // ObjectId
            foreignField: "_id",
            as: "user"
        }
    },
    { $unwind: "$user" },
    {
        $project: {
            _id: 0,
            tagged_user_id: "$user.user_id",
            username: "$user.username",
            country: "$user.country",
            tagCount: 1
        }
    }
]).forEach(printjson);;


// ---------------------------------------------------------------------------------------------
// Task 7
// ---------------------------------------------------------------------------------------------
print("Task 7")
db.posts.aggregate([
    {
        $match: {
            created_at: { $gte: ISODate("2022-12-02T00:00:00Z") },
            tags: { $ne: [] },
            group: { $ne: null }
        }
    },
    { $unwind: "$tags" },
    {
        $group: {
            _id: "$group",             // group ObjectId
            tagCount: { $sum: 1 }
        }
    },
    { $sort: { tagCount: -1 } },
    { $limit: 10 },
    {
        $lookup: {
            from: "groups",
            localField: "_id",
            foreignField: "_id",
            as: "group"
        }
    },
    { $unwind: "$group" },
    {
        $project: {
            _id: 0,
            group_id: "$group.group_id",
            group_name: "$group.name",
            tagCount: 1
        }
    }
]).forEach(printjson);;


// ---------------------------------------------------------------------------------------------
// Task 8
// ---------------------------------------------------------------------------------------------
print("Task 8")
db.comments.aggregate([
    {
        $match: {
            written_at: { $gte: ISODate("2022-10-03T00:00:00Z") }
        }
    },
    {
        $lookup: {
            from: "posts",
            localField: "post",        // post ObjectId
            foreignField: "_id",
            as: "post"
        }
    },
    { $unwind: "$post" },
    {
        $lookup: {
            from: "users",
            localField: "post.user",   // creator of the post
            foreignField: "_id",
            as: "postCreator"
        }
    },
    { $unwind: "$postCreator" },
    {
        $match: {
            "postCreator.is_commercial": 1   // keep only ad posts
        }
    },
    {
        $group: {
            _id: "$user",                    // commenter ObjectId
            adEngagementCount: { $sum: 1 }
        }
    },
    { $sort: { adEngagementCount: -1 } },
    { $limit: 10 },
    {
        $lookup: {
            from: "users",
            localField: "_id",
            foreignField: "_id",
            as: "user"
        }
    },
    { $unwind: "$user" },
    {
        $project: {
            _id: 0,
            user_id: "$user.user_id",
            username: "$user.username",
            country: "$user.country",
            adEngagementCount: 1
        }
    }
]).forEach(printjson);;


// ---------------------------------------------------------------------------------------------
// Task 12
// ---------------------------------------------------------------------------------------------
print("Task 12")
db.posts.aggregate([
    {
        $match: {
            activity: ObjectId("000000000000000000000032")   // activity 50
        }
    },
    {
        $group: {
            _id: "$user",           // user ObjectId
            attempts: { $sum: 1 },
            firstAttempt: { $min: "$created_at" },
            lastAttempt: { $max: "$created_at" }
        }
    },
    { $sort: { attempts: -1 } },
    {
        $lookup: {
            from: "users",
            localField: "_id",
            foreignField: "_id",
            as: "user"
        }
    },
    { $unwind: "$user" },
    {
        $project: {
            _id: 0,
            user_id: "$user.user_id",
            username: "$user.username",
            attempts: 1,
            firstAttempt: 1,
            lastAttempt: 1
        }
    }
]).forEach(printjson);;


// ---------------------------------------------------------------------------------------------
// Task 14
// ---------------------------------------------------------------------------------------------
print("Task 14")
db.posts.aggregate([
    {
        $match: {
            activity: { $ne: null },
            created_at: { $gte: ISODate("2021-01-01T00:00:00Z") }
        }
    },
    {
        $lookup: {
            from: "activities",
            localField: "activity",
            foreignField: "_id",
            as: "activity"
        }
    },
    { $unwind: "$activity" },
    {
        $addFields: {
            month: { $month: "$created_at" }
        }
    },
    {
        $addFields: {
            season: {
                $switch: {
                    branches: [
                        { case: { $in: ["$month", [3, 4, 5]] }, then: "spring" },
                        { case: { $in: ["$month", [6, 7, 8]] }, then: "summer" },
                        { case: { $in: ["$month", [9, 10, 11]] }, then: "autumn" }
                    ],
                    default: "winter"
                }
            },
            weather: {
                $cond: [
                    { $lt: ["$activity.base_elev_m", 300] }, "lowland",
                    {
                        $cond: [
                            { $lt: ["$activity.base_elev_m", 800] }, "mid-altitude",
                            "high-altitude"
                        ]
                    }
                ]
            }
        }
    },
    {
        $group: {
            _id: {
                activity_id: "$activity.activity_id",
                season: "$season",
                weather: "$weather"
            },
            attempts: { $sum: 1 },
            avg_distance_m: { $avg: "$activity.distance_m" },
            avg_total_elev_m: { $avg: "$activity.total_elev_m" }
        }
    },
    { $sort: { attempts: -1 } }
]).forEach(printjson);;


// ---------------------------------------------------------------------------------------------
// Task 15
// ---------------------------------------------------------------------------------------------
print("Task 15")
db.users.createIndex({ join_date: 1 });
db.posts.createIndex({ created_at: 1 });

var startDate = ISODate("2022-11-01T00:00:00Z");
var endDate = ISODate("2022-12-31T23:59:59Z");

db.users.aggregate([
    {
        $match: {
            join_date: { $gte: startDate, $lt: endDate }
        }
    },
    { $limit: 20 },
    {
        $addFields: {
            deadline: { $add: ["$join_date", 7 * 24 * 60 * 60 * 1000] }
        }
    },
    {
        $addFields: {
            joined_first_group: {
                $gt: [
                    {
                        $size: {
                            $filter: {
                                input: "$joined_groups",
                                as: "g",
                                cond: { $lte: ["$$g.joined_at", "$deadline"] }
                            }
                        }
                    }, 0
                ]
            }
        }
    },
    {
        $lookup: {
            from: "posts",
            localField: "created_posts",
            foreignField: "_id",
            as: "post_details"
        }
    },
    {
        $addFields: {
            completed_first_share: {
                $gt: [
                    {
                        $size: {
                            $filter: {
                                input: "$post_details",
                                as: "p",
                                cond: { $lte: ["$$p.created_at", "$deadline"] }
                            }
                        }
                    }, 0
                ]
            }
        }
    },
    {
        $project: {
            _id: 0,
            username: 1,
            join_date: 1,
            country: 1,
            completed_first_share: 1,
            joined_first_group: 1
        }
    },
    { $sort: { join_date: 1 } }

]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 16
// ---------------------------------------------------------------------------------------------
print("Task 16")
db.posts.createIndex({ created_at: 1 });
db.comments.createIndex({ written_at: 1 });

var referenceDate = ISODate("2022-12-31T23:59:59Z");
var startDate = new Date(referenceDate - 90 * 24 * 60 * 60 * 1000);

db.posts.aggregate([
    {
        $match: {
            created_at: { $gte: startDate, $lte: referenceDate }
        }
    },
    {
        $project: { timestamp: "$created_at", type: "post" }
    },
    {
        $unionWith: {
            coll: "comments",
            pipeline: [
                { $match: { written_at: { $gte: startDate, $lte: referenceDate } } },
                { $project: { timestamp: "$written_at", type: "comment" } }
            ]
        }
    },
    {
        $project: {
            day: { $dayOfWeek: "$timestamp" },
            hour: { $hour: "$timestamp" }
        }
    },
    {
        $group: {
            _id: { day: "$day", hour: "$hour" },
            total_interactions: { $sum: 1 }
        }
    },
    { $sort: { total_interactions: -1 } },
    { $limit: 5 },
    {
        $project: {
            _id: 0,
            day_of_week: "$_id.day",
            hour_of_day: "$_id.hour",
            total_interactions: 1
        }
    }

]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 19
// ---------------------------------------------------------------------------------------------
print("Task 19")
db.users.createIndex({ country: 1 });
db.activities.createIndex({ country: 1 });

db.users.aggregate([

    {
        $group: {
            _id: "$country",
            userCount: { $sum: 1 }
        }
    },
    {
        $lookup: {
            from: "activities",
            localField: "_id",
            foreignField: "country",
            as: "paths_in_region"
        }
    },
    {
        $project: {
            region: "$_id",
            active_users: "$userCount",
            path_count: { $size: "$paths_in_region" },
            _id: 0
        }
    },
    {
        $project: {
            region: 1,
            active_users: 1,
            path_count: 1,
            user_to_path_ratio: {
                $cond: {
                    if: { $eq: ["$path_count", 0] },
                    then: 0,
                    else: { $divide: ["$active_users", "$path_count"] }
                }
            }
        }
    },
    { $sort: { user_to_path_ratio: -1 } },
    { $limit: 10 }

]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 20
// ---------------------------------------------------------------------------------------------
print("Task 20")
db.users.createIndex({ join_date: 1 });

var referenceDate = ISODate("2023-01-01T00:00:00Z");
var startDate = new Date(referenceDate - 90 * 24 * 60 * 60 * 1000);

db.users.aggregate([
    {
        $match: {
            join_date: { $gte: startDate, $lte: referenceDate }
        }
    },
    {
        $project: {
            step1_registered: { $literal: 1 },

            step2_joined: {
                $cond: [{ $gt: [{ $size: "$joined_groups" }, 0] }, 1, 0]
            },
            step3_posted: {
                $cond: [{ $gt: [{ $size: "$created_posts" }, 0] }, 1, 0]
            }
        }
    },
    {
        $group: {
            _id: null,
            total_reg: { $sum: "$step1_registered" },
            total_join: { $sum: "$step2_joined" },
            total_post: { $sum: "$step3_posted" }
        }
    },
    {
        $project: {
            _id: 0,
            steps: [
                {
                    step: "1. Registered",
                    count: "$total_reg",
                    rate: "100%"
                },
                {
                    step: "2. Joined First Group",
                    count: "$total_join",
                    rate: {
                        $concat: [
                            { $toString: { $multiply: [{ $divide: ["$total_join", "$total_reg"] }, 100] } },
                            "%"
                        ]
                    }
                },
                {
                    step: "3. Created First Post",
                    count: "$total_post",
                    rate: {
                        $concat: [
                            { $toString: { $multiply: [{ $divide: ["$total_post", "$total_reg"] }, 100] } },
                            "%"
                        ]
                    }
                }
            ]
        }
    },
    { $unwind: "$steps" },
    { $replaceRoot: { newRoot: "$steps" } }
]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 21
// ---------------------------------------------------------------------------------------------
print("Task 21")
db.groups.createIndex({ last_activity: 1 });

var referenceDate = ISODate("2023-01-01T00:00:00Z");
var thresholdDate = new Date(referenceDate - 60 * 24 * 60 * 60 * 1000);

db.groups.aggregate([
    {
        $match: {
            last_activity: { $lt: thresholdDate }
        }
    },
    {
        $lookup: {
            from: "users",
            localField: "_id",
            foreignField: "joined_groups.group_id",
            as: "members"
        }
    },
    {
        $project: {
            _id: 0,
            group_id: "$_id",
            group_name: "$name",
            member_count: { $size: "$members" },

            days_since_last_activity: {
                $floor: {
                    $divide: [
                        { $subtract: [referenceDate, "$last_activity"] },
                        1000 * 60 * 60 * 24
                    ]
                }
            }
        }
    },
    { $sort: { days_since_last_activity: -1 } }
]).forEach(printjson);

// ---------------------------------------------------------------------------------------------

